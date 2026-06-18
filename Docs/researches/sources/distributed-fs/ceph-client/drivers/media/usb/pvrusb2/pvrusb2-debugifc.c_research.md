<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-debugifc.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-debugifc.c

Purpose: sysfs-hosted debug command and status implementation for pvrusb2.

Important APIs/types/functions: `pvr2_debugifc_print_info()` emits hardware description and state report. `pvr2_debugifc_print_status()` reports USB speed, GPIO state, streaming state, and stream buffer stats. `pvr2_debugifc_docmd()` parses newline-separated commands. Internal helpers tokenize whitespace, parse unsigned numbers in decimal/octal/hex, and match keywords. Supported commands include reset variants, CPU firmware fetch/done, GPIO direction/output changes, stream stats reset, firmware reload, decoder reset, and worker untrip.

Control flow: sysfs/debug code passes user text to `pvr2_debugifc_docmd()`, which splits lines and executes each command with `pvr2_debugifc_do1cmd()`. Commands call into the hardware layer for resets, GPIO changes, firmware upload, and stream statistic reset. Print functions query hardware and stream state into caller-provided buffers.

State and persistence: no private state. Commands can mutate persistent hardware state: reset lines, GPIO direction/output, firmware capture mode, powerup/deep reset, and worker/stream stats.

Dependencies and integration: depends on pvrusb2 hardware API, stream stats, debug masks, and Linux hex parsing. It is compiled only when the debug interface option is selected through Kconfig/Makefile.

Risks: debug commands are intentionally intrusive and can reset hardware or alter GPIOs. Number parsing manually handles radix and overflow is not explicitly checked. `print_info()` can synchronize with hardware and comments warn it may hang if the driver is wedged. Command grammar is minimal and returns `-EINVAL` on many partial inputs.

Test signals: with `VIDEO_PVRUSB2_DEBUGIFC`, read info/status sysfs files; issue safe commands like `reset usbstats`; validate GPIO command parsing with mask/value forms; verify restricted/debug-only exposure; test invalid commands returning errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-debugifc.c -->
