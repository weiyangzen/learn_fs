## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-common-powernv.c

Purpose: provides the PowerNV hardware backend for NX 842 compression. It discovers NX coprocessors from the device tree, chooses either legacy ICSWX submission or Power9+ VAS copy/paste submission, registers the `842` scomp algorithm, and supplies the shared `nx-842.c` layer with hardware constraints and function pointers.

Important types and functions: `struct nx842_workmem` contains aligned CRB and DDLs. `struct nx_coproc` tracks chip, coprocessor type/instance, and VAS receive window. Submission helpers include `setup_direct_dde`, `setup_indirect_dde`, `setup_ddl`, `nx842_config_crb`, `nx842_exec_icswx`, `nx842_exec_vas`, and `wait_for_csb`. Discovery/setup includes `nx_powernv_probe_vas`, `nx842_powernv_probe`, `nx_open_percpu_txwins`, `vas_cfg_coproc_info`, and `nx_coproc_init`.

Control flow: module init verifies alignment assumptions, scans `ibm,power9-nx` nodes for VAS FIFOs, initializes coprocessors through OPAL, registers a VAS userspace API for GZIP, and opens per-CPU TX windows for 842. If no VAS coprocessors are found, it scans legacy `ibm,power-nx` nodes and uses ICSWX. Compression/decompression wrappers pass CRC function codes into the selected exec function. Each exec builds DDE/DDL descriptors, submits the CRB, waits for CSB validity, maps completion codes to Linux errors, and returns processed length.

State and persistence: runtime state is global `nx_coprocs`, per-CPU `cpu_txwin`, `nx842_ct`, the selected `nx842_powernv_exec` function pointer, and registered scomp algorithm state. No persistent storage exists.

Dependencies: PowerNV OF nodes, OPAL NX initialization, VAS APIs, ICSWX, PowerPC physical address helpers, CSB/CRB definitions, crypto scomp API, and shared `nx-842.c` exports.

Risks: per-CPU VAS windows assume each CPU maps to a chip with a high-priority 842 FIFO. DDE setup enforces alignment and length constraints; relaxing constraints risks hardware checkstops or protocol errors. `wait_for_csb` busy-waits up to 5 seconds, so hung hardware impacts CPU time. VAS retry handling and preemption disabling are sensitive. Init cleanup must close RX/TX windows on every failure path.

Test signals: boot tests on Power8 ICSWX and Power9+ VAS systems, DT missing-property failures, OPAL failure handling, per-CPU TX window setup, malformed CSB code mapping, compression/decompression scomp vectors, busy/timeout paths, module unload window cleanup, and fallback to legacy path when VAS nodes are absent.
