## sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/Makefile

### Purpose
This Makefile builds PIC32MZDA platform support objects and optional early printk support.

### Important APIs, Types, And Functions
Base objects are `config.o`, `early_clk.o`, `init.o`, and `time.o`. With `CONFIG_EARLY_PRINTK`, it also builds `early_console.o` and `early_pin.o`.

### Control Flow
Build rules follow Kconfig. Early console pin and UART setup are absent unless early printk is configured.

### State, Persistence, And Dependencies
No runtime state exists in the Makefile. Object selection depends on `CONFIG_PIC32MZDA` and `CONFIG_EARLY_PRINTK`.

### Integration Points
The built objects provide machine identity, DT population, clocks, reset-protected config registers, timer frequency, and early UART output.

### Risks
Disabling early printk removes early pin/UART setup, which can make bring-up failures harder to diagnose.

### Test Signals
Build with early printk enabled and disabled; verify symbol availability for `fw_init_early_console()` only when expected.
