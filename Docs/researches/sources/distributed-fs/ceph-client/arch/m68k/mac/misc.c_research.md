# sources/distributed-fs/ceph-client/arch/m68k/mac/misc.c

## Purpose
Provides Macintosh-specific PRAM/NVRAM, RTC, poweroff, reset, and hardware-clock support.

## APIs, Flow, And State
Public APIs include `mac_pram_read_byte()`, `mac_pram_write_byte()`, `mac_pram_get_size()`, `mac_poweroff()`, `mac_reset()`, and `mac_hwclk()`. The file stores a `rom_reset` function pointer and uses model state to choose VIA RTC, CUDA, or PMU backends. VIA RTC commands bit-bang VIA1 port B lines with interrupts disabled, support one-byte and extended XPRAM commands, and clear/set write-protect around writes. `via_read_time()` repeatedly reads four RTC second registers until stable and subtracts the 1904-to-1970 offset. Reset uses CUDA/PMU when possible, otherwise a 68030 transparent-translation sequence or ROM reset vector.

## Dependencies And Integration
Depends on Mac ADB type from `macintosh_config`, VIA/OSS globals, CUDA/PMU APIs, m68k MMU/cache registers, `machdep` hooks, and Linux RTC/time helpers. `config_mac()` wires these functions into `mach_hwclk`, `mach_reset`, and `mach_halt`.

## Risks And Test Signals
RTC reads can fail to stabilize; CUDA shutdown intentionally avoids infinite polling on models whose PSU is not CUDA-controlled. Reset code is CPU- and mapping-sensitive and disables interrupts before MMU/register manipulation. Test signals are PRAM read/write, stable clock reads/writes, shutdown behavior on VIA/OSS/CUDA/PMU systems, and successful reset on 030 and non-030 machines.
