# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/prom.c

## Purpose
`prom.c` handles early firmware/PROM initialization for Alchemy boards using YAMON- or U-Boot-style arguments. It captures firmware argc/argv/envp pointers, constructs the kernel command line, discovers RAM size, registers memory with memblock, reads firmware environment variables, and parses Ethernet MAC addresses.

## Important APIs, Types, And Functions
Global firmware argument state is `prom_argc`, `prom_argv`, and `prom_envp`. Public functions are `prom_init_cmdline()`, `prom_getenv()`, `prom_init()`, and `prom_get_ethernet_addr()`. Helpers `str2hexnum()` and `str2eaddr()` parse textual MAC bytes. The file uses `fw_arg0`, `fw_arg1`, `fw_arg2`, `arcs_cmdline`, and `memblock_add()`.

## Control Flow
`prom_init()` stores firmware arguments from CPU registers, calls `prom_init_cmdline()` to concatenate argv entries 1..N into `arcs_cmdline`, reads `memsize` from the firmware environment, defaults to 64 MiB if missing or invalid, and registers RAM from physical 0 through `memsize`. `prom_getenv()` detects YAMON name/value-pair environment format versus U-Boot `name=value` format, then scans for the requested key. `prom_get_ethernet_addr()` checks `ethaddr` in the environment first, falls back to `ethaddr=` in the command line, and parses the address.

## State And Persistence
The persistent early-boot state is the command line, memblock memory range, and retained pointers to firmware argument/environment arrays. Parsed Ethernet addresses are copied into caller buffers. The file does not allocate memory or preserve environment variables beyond the original firmware-provided strings.

## Dependencies And Integration Points
It depends on MIPS bootinfo firmware argument registers, `arcs_cmdline`, memblock, kernel string helpers, and Alchemy platform code. `platform.c` calls `prom_get_ethernet_addr()` to seed Ethernet MAC addresses. Board code provides `prom_putchar()` for early output, while this file handles firmware data.

## Risks
Firmware pointers must remain valid during early boot; malformed envp arrays can break scanning. `prom_init_cmdline()` appends argv strings without quoting and truncates only through `strlcat` behavior. `memsize` defaults to 64 MiB, which may underreport or overassume on unusual boards. `str2eaddr()` treats invalid hex characters as zero and does not validate separators or length, so malformed MAC strings can produce plausible but invalid addresses. `prom_get_ethernet_addr()` does not call `is_valid_ether_addr()`, leaving validation to callers.

## Test Signals
Boot with YAMON-style and U-Boot-style environments and verify command-line construction, `memsize` parsing, and fallback to 64 MiB on invalid input. Test `ethaddr` from env and command line using colon and dot separators. Confirm Ethernet platform code rejects invalid MACs if needed. Early boot should show the expected memblock region in boot logs or memory debug output.
