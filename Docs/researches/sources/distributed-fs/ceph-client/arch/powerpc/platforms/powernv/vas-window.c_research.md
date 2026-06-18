## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas-window.c

### Purpose
`vas-window.c` implements PowerNV VAS window lifecycle and operations: allocating window IDs, mapping context/paste regions, programming HV/UW window registers, opening RX/TX windows, paste/copy helpers, credit handling, close sequencing, PSWID lookup, and user API registration.

### Important APIs, Types, And Functions
Public/exported functions include `vas_win_paste_addr()`, `vas_init_rx_win_attr()`, `vas_rx_win_open()`, `vas_init_tx_win_attr()`, `vas_tx_win_open()`, `vas_copy_crb()`, `vas_paste_crb()`, `vas_win_close()`, `vas_return_credit()`, `vas_pswid_to_window()`, `vas_register_api_powernv()`, and `vas_unregister_api_powernv()`. Internal helpers manage MMIO mapping, register initialization, window tables, RX references, and close polling.

### Control Flow
Window allocation reserves an ID from the instance IDA, maps HVWC/UWC MMIO bars, and creates debugfs entries. RX open validates attributes, programs context for NX, fault, or FTW receive windows, and records the window in instance lookup tables. TX open validates attributes, resolves the matching RX window, programs translation/credit/fault/PSWID registers, maps a kernel paste page for kernel windows or attaches user mm context for user windows, and records the window. Paste uses the copy/paste instruction wrapper and optional report-enable offset. Close unmaps paste, waits for not-busy and credits, clears open/pin bits, removes table entries, drops RX/user references, and frees mappings/ID.

### State, Persistence, And Dependencies
State spans `struct pnv_vas_window`, instance `windows[]`/`rxwin[]` tables, IDA allocations, hardware window context registers, paste mappings, debugfs entries, RX reference counts, task/mm references for user windows, and hardware credits. Dependencies include VAS workbook register layouts, `copy-paste.h`, MMIO, IRQ/fault support, mm context VAS helpers, and the generic `asm/vas.h` API.

### Integration Points
NX compression/GZIP and user coprocessor APIs open windows through these exports. Fault handling uses PSWID lookup and credit return. `vas.c` provides instances and IRQ ports.

### Risks
Close waits can stall indefinitely if hardware credits or busy state do not clear. Mapping errors must unwind RX references and IDs. User windows require successful fault IRQ setup. Register programming order matters because `WINCTL_OPEN` is written last.

### Test Signals
Kernel NX requests, user NX-GZIP mmap/open/close, credit exhaustion, paste success/failure return codes, fault-window paths, debugfs lifecycle, and concurrent open/close stress are key tests.
