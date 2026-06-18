## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas-fault.c

### Purpose
`vas-fault.c` handles NX/VAS translation faults for user send windows through a per-VAS fault receive window and FIFO.

### Important APIs, Types, And Functions
Important functions are threaded IRQ handler `vas_fault_thread_fn()`, hard IRQ handler `vas_fault_handler()`, fault FIFO diagnostic `dump_fifo()`, and `vas_setup_fault_window()`.

### Control Flow
Instance setup allocates a 4 MiB fault FIFO, invalidates CRB slots, initializes a `VAS_COP_TYPE_FAULT` receive window, and stores it in the instance. The IRQ handler uses `fault_lock` and `fifo_in_progress` to wake only one thread. The thread walks FIFO CRBs until it reaches an invalid entry, copies each CRB, invalidates the slot, returns fault-window credit, resolves the PSWID to a user send window, updates the user completion/status block, and returns send-window credit.

### State, Persistence, And Dependencies
State is `fault_fifo`, `fault_crbs`, `fault_fifo_size`, `fault_win`, `fifo_in_progress`, and credit registers in VAS hardware. Dependencies include CRB layout, `vas_update_csb()`, `vas_pswid_to_window()`, and VAS credit return helpers.

### Integration Points
`vas.c` requests the threaded IRQ and calls `vas_setup_fault_window()`. `vas-window.c` points user send windows at the fault window when an IRQ is available.

### Risks
Invalid PSWIDs imply lost ability to return user credits. FIFO pointer wrap and CRB invalidation must match hardware. Continuous faults rely on `fifo_in_progress` to avoid missed work.

### Test Signals
User NX-GZIP page faults, multiple CRBs per interrupt, FIFO wrap, credit restoration, bad PSWID diagnostics, and user-window close while faults are pending are high-value tests.
