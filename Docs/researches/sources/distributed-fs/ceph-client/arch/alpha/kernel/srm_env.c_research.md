# sources/distributed-fs/ceph-client/arch/alpha/kernel/srm_env.c

## Purpose
`srm_env.c` exposes Alpha SRM firmware environment variables through procfs. It creates named and numbered proc entries, reads variables through SRM callbacks, writes variables through callback set/save operations, and loads only on systems detected as SRM-booted.

## Important APIs, Types, And Functions
- Proc layout constants create `/proc/srm_environment/named_variables` and `/proc/srm_environment/numbered_variables`.
- `srm_env_t` maps human-readable names to SRM environment IDs.
- `srm_named_entries[]` includes variables such as `auto_action`, boot device/file/flags, dump device, audit, license, charset, language, and `tty_dev`.
- `srm_env_proc_show()` allocates a page, calls `callback_getenv()`, and writes returned bytes to seq_file when callback status is successful.
- `srm_env_proc_open()` binds `pde_data()` as the variable ID.
- `srm_env_proc_write()` copies user input, calls `callback_setenv()`, then loops on `callback_save_env()` while status indicates busy.
- `srm_env_proc_ops` wires open/read/lseek/release/write.
- `srm_env_init()` validates `alpha_using_srm`, creates proc directories and entries, and handles cleanup on failure.
- `srm_env_exit()` removes the proc subtree.

## Control Flow
Module init rejects non-SRM systems. It creates the base directory, named subdirectory, numbered subdirectory, all named entries with their IDs, then entries `0` through `255` for raw variable numbers. Reads allocate a temporary page and decode SRM callback status from the top three bits of the returned value. Writes reject page-sized or larger input, NUL-terminate the copied buffer, set the variable, and save the environment until firmware is no longer busy.

## State And Persistence
Kernel state consists of proc directory entries and static variable tables. Writes persist into SRM firmware environment storage through `callback_save_env()`, so they survive reboot depending on firmware behavior. Temporary pages are allocated per read/write.

## Dependencies And Integration Points
The module depends on SRM callback APIs, `alpha_using_srm` from setup, procfs, seq_file, module init/exit, and user-copy helpers. It is an optional firmware-management interface for user space.

## Risks
- Firmware callbacks can fail or return status-encoded values; the code treats any top status bits as `-EFAULT`.
- Write loops on `callback_save_env()` while busy with no explicit timeout.
- Proc entry creation failures trigger subtree cleanup, but partially visible entries can exist briefly during init.
- User input is passed to firmware with its original `count`, including any newline written by shell tools.

## Test Signals
- On SRM systems, `/proc/srm_environment` appears with named and numbered variables.
- Reading known variables returns firmware values.
- Writing a safe test variable changes SRM state and survives a save.
- On non-SRM/MILO systems, module init returns `-ENODEV`.
- Error injection for proc creation cleans up the subtree.
