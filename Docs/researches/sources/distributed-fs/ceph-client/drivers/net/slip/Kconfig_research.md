# sources/distributed-fs/ceph-client/drivers/net/slip/Kconfig

Purpose: defines configuration for the SLIP serial-line network driver and related optional modes.

Important options: `SLIP` is a tristate depending on `TTY` and builds the core serial line IP driver. `SLHC` is a hidden tristate for Van Jacobsen TCP/IP header compression helpers. `SLIP_COMPRESSED` depends on `SLIP` and selects `SLHC` to enable CSLIP compressed headers. `SLIP_SMART` enables keepalive and line-fill support. `SLIP_MODE_SLIP6` enables six-bit SLIP encapsulation for links that cannot pass full 8-bit data.

Control flow: the compression, smart keepalive, and SLIP6 options are visible only inside `if SLIP`. Enabling compressed SLIP automatically selects the helper module used by the driver. The Makefile uses `CONFIG_SLIP` and `CONFIG_SLHC` to include the actual objects.

State and persistence: no runtime state is defined here. Symbol choices determine which code paths and module objects are present in the kernel build.

Dependencies and integration: connects the SLIP networking driver to the TTY subsystem and compression helper object. Help text documents operational expectations and legacy use cases such as SLiRP and poor serial links.

Risks and test signals: risks are hidden-helper mismatch if compressed mode does not select `SLHC`, unmet TTY dependencies, and untested legacy mode combinations. Test signals include builds for SLIP as module/built-in, compressed mode selecting `slhc.o`, smart and SLIP6 option compilation, and disabled SLIP hiding optional features.
