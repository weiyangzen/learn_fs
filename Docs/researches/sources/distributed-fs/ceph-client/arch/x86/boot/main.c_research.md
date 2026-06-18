# sources/distributed-fs/ceph-client/arch/x86/boot/main.c

Purpose: orchestrates real-mode setup before jumping to protected mode.

Important APIs and state: defines aligned global `struct boot_params boot_params`, `struct port_io_ops pio_ops`, heap pointers `HEAP` and `heap_end`, and entry `main()`. Local helpers copy boot params, initialize keyboard, query Intel SpeedStep IST, tell BIOS intended long mode, and initialize heap bounds.

Control flow: `main()` initializes default I/O ops, copies header fields into zeropage, initializes console, optionally prints debug, bounds heap, validates CPU, notifies BIOS of mode, detects memory, initializes keyboard, queries IST/APM/EDD, selects video, and calls `go_to_protected_mode()`.

Dependencies and integration: entered from `header.S`. It feeds `boot_params` to later protected-mode/compressed kernel stages. Depends on BIOS interrupts, command-line parsing, CPU/memory/video modules, and `pm.c`.

Risks and test signals: order matters: console before diagnostics, CPU validation before mode switch, memory/video before boot_params handoff. Test legacy and modern bootloaders, old command-line protocol conversion, heap-limited boots, debug output, and all configured optional probe paths.
