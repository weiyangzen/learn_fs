# sources/distributed-fs/ceph-client/fs/proc/cmdline.c

Purpose: Registers `/proc/cmdline`, exposing the saved kernel command line.

Important APIs and types: Uses `saved_command_line`, `saved_command_line_len`, `proc_create_single()`, `pde_make_permanent()`, and `struct proc_dir_entry`.

Control flow: `proc_cmdline_init()` creates a single-read proc file named `cmdline`, marks it permanent, and sets its size to the command-line length plus newline. `cmdline_proc_show()` writes the saved command line and a trailing newline.

State and persistence: The file reflects the boot-time `saved_command_line`; it does not change after initialization.

Dependencies and integration points: Built as a core proc object and registered at `fs_initcall`. Uses proc generic helpers and seq_file output.

Risks: Assumes proc entry creation succeeds before dereferencing the returned `pde`. Size metadata must match the emitted newline. The command line may include sensitive boot parameters, so access mode and system policy matter.

Test signals: Boot with empty and long command lines, verify size/read output and permanent-entry behavior, and ensure `/proc/cmdline` exists when procfs is enabled.
