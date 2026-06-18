<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_cfg.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_cfg.h

## Purpose
`stb0899_cfg.h` provides reusable static initialization tables and DVB-S2 tuning constants for the STB0899 driver. It is data, not executable logic, but it directly shapes hardware initialization and acquisition behavior.

## Important APIs, Types, And Functions
The file defines `stb0899_s2_init_2[]` for S2 demodulator initialization, `stb0899_s2_init_4[]` for S2 FEC initialization, and `stb0899_s1_init_5[]` for S1/test register initialization. Each table ends with a sentinel (`0xffff`, `0xffffffff`) consumed by loops in `stb0899_init()`. It also defines default DVB-S2 parameters such as Es/N0 averaging/quantization, coarse/fine acquisition frame counts, miss thresholds, UWP thresholds, SOF search timeout, BTR/CRL NCO widths, gain-shift offset, and LDPC max iterations.

## Control Flow
Board-specific `struct stb0899_config` instances can point at these tables. During frontend `.init`, `stb0899_drv.c` iterates each configured table and writes S1 registers or S2 base/offset/data triples. Later, `stb0899_algo.c` reads the constants through config fields to program UWP, BTR, CRL, and LDPC behavior.

## State And Persistence
The tables are immutable static data compiled into the module. Once written, their values persist in hardware registers until reprogrammed. The constants are usually copied into board config fields, then used repeatedly during searches.

## Dependencies And Integration Points
The file relies on `stb0899_drv.h` table types and `stb0899_reg.h` register macros being visible to includers. It integrates initialization data with the driver proper and board configuration.

## Risks And Test Signals
Risks are table drift against silicon revisions, wrong sentinel placement, and parameter values that work for one board clock/tuner path but not another. Because this header defines static objects, including it in multiple C files would create duplicate private copies; it should be included only where intended by board code. Test signals are clean init-table completion, readable S2 demod/FEC core IDs after wake, DVB-S2 lock stability across modcods, and no writes past sentinel values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_cfg.h -->
