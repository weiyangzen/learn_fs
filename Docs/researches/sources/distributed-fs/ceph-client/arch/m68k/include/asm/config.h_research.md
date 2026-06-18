<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/config.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/config.h

## Purpose
This header declares platform-specific bootinfo parsers and configuration entry points for the m68k machine families.

## Important APIs, Types, And Functions
- Bootinfo parsers: `amiga_parse_bootinfo()`, `apollo_parse_bootinfo()`, `atari_parse_bootinfo()`, `bvme6000_parse_bootinfo()`, `hp300_parse_bootinfo()`, `mac_parse_bootinfo()`, `mvme147_parse_bootinfo()`, `mvme16x_parse_bootinfo()`, `q40_parse_bootinfo()`, and `virt_parse_bootinfo()`.
- Configuration functions: `config_amiga()`, `config_apollo()`, `config_atari()`, `config_bvme6000()`, `config_hp300()`, `config_mac()`, `config_mvme147()`, `config_mvme16x()`, `config_q40()`, `config_sun3()`, `config_sun3x()`, and `config_virt()`.

## Control Flow
Early architecture setup selects the active machine, parses boot records through the relevant parser, then calls the matching `config_*()` function to initialize platform callbacks, memory, devices, and IRQs.

## State And Persistence Behavior
State is mutated by the implementations: machine globals, memory layout, platform hooks, device resources, and parsed bootinfo. The header declares the dispatch surface only.

## Dependencies And Integration Points
It depends on `struct bi_record` from bootinfo headers and integrates with arch setup for all supported m68k platforms.

## Risks And Edge Cases
Missing declarations or wrong parser signatures break early boot. Platform config functions have global side effects and must be called exactly for the detected machine.

## Test Signals
Boot each machine family config far enough to parse bootinfo and register platform devices/IRQs. Build coverage across enabled/disabled platform combinations catches declaration drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/config.h -->
