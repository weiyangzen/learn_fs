## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_ras.c

Purpose: Implements Gen4 Reliability, Availability, and Serviceability operations: enabling/disabling hardware error reporting and demultiplexing RAS interrupts into logs, counters, CSR clears, and reset-required decisions.

Important APIs/functions: `adf_gen4_init_ras_ops()` installs `enable_ras_errors`, `disable_ras_errors`, and `handle_interrupt`. Enable/disable helpers program ERRSOU masks, AE logs, CPP command parity, RI/TI parity, RF parity, SSM error handling, and ARAM ECC/error controls. `adf_gen4_handle_interrupt()` reads ERRSOU0..3 and dispatches to `adf_gen4_process_errsou0/1/2/3()`.

Control flow and state: ERRSOU0 handles correctable AE errors. ERRSOU1 handles AE uncorrectable, CPP command parity, RI memory parity, TI memory parity groups, and IOSFP command parity. ERRSOU2 handles SSM and CPP CFC errors. ERRSOU3 handles TI misc, RI/TI CPP interface, ARAM correctable/uncorrectable, ARAM memory target, and ATU faults. Handlers increment `accel_dev->ras_errors` counters, log with `dev_warn` or `dev_err`, clear status CSRs by writing the observed bits, and OR fatal conditions into `*reset_required`.

Dependencies/integration: Depends on Gen4 hardware and RAS headers, ARAM and PMISC BAR mappings, `adf_sysfs_ras_counters`, and per-device error masks from `GET_ERR_MASK()`. It is called from the common interrupt/RAS handling path.

Risks and test signals: The code is register-mask dense; risks include over-clearing status, missing optional WAT/WCP masks, misclassifying fatal versus uncorrectable errors, and reset-required decisions drifting from hardware requirements. Tests should inject or emulate ERRSOU bits for each group, verify counter class increments, verify status clear writes, confirm optional mask behavior, and check that fatal SPP command, SSM CPP fatal, CPP CFC command/multiple, RI fatal, TIMISC, and ARAM multiple errors request reset.
