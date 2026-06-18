## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_ras.c

Purpose: Implements Gen6 RAS enable/disable and interrupt handling for correctable, uncorrectable, and fatal hardware errors.

Important APIs/functions: `adf_gen6_init_ras_ops()` installs Gen6 RAS callbacks. Enable/disable helpers program ERRSOU masks, AE logs, CPP command parity, CPP CFC control, RI/TI parity, TIMISC, RI/TI CPP interface controls, and SSM interrupt masks. `adf_gen6_handle_interrupt()` reads ERRSOU0..3, dispatches to processors, and then calls `adf_gen6_is_reset_required()`.

Control flow and state: ERRSOU0 handles correctable AE logs. ERRSOU1 handles AE uncorrectable, CPP command parity, RI memory parity, TI parity group, IOSFP command parity, and SFI command parity. ERRSOU2 handles SSM and CPP CFC. ERRSOU3 handles TI misc, RI/TI CPP interface errors, ATU faults, rate-limiting block errors, VFLR, PCIe TC/VC mapping, PCIe/page-request/translation DEVHALT, and TI internal DEVHALT. Handlers log, increment `accel_dev->ras_errors`, and clear status CSRs. After processing, the reset decision is derived from `GENSTS`: PFLR is required when device state is DEVHALT and reset type is PFLR; cold reset is logged but `reset_required` is false for that path.

Dependencies/integration: Depends on `adf_gen6_ras.h` constants, PMISC mapping, bitfield helpers, and sysfs RAS counters. Compared with Gen4 it does not use ARAM BAR helpers and has a hardware-state based reset decision.

Risks and test signals: Important risks are status bits remaining set after handler clears, severity classification, and reset decision interpretation from `GENSTS`. Tests should inject each ERRSOU group, verify counter classes and clear writes, check warnings for still-set ERRSOU registers, and cover GENSTS DEVHALT/PFLR and cold-reset cases.
