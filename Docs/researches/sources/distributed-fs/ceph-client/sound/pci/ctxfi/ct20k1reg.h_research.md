# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ct20k1reg.h

Purpose: register-address map for the Creative 20K1 X-Fi hardware backend.

Important APIs and types: defines DSP RAM/register ranges, transport registers, audio ring and mapper ranges, mixer operator registers, SRC/SRC manager registers, filter ranges, DAIO registers (`DAOIMAP`, `SPOS`, `SRTSCTL`, `I2SCTL`, `SPICTL`, `SPOCTL`), timer/global interrupt registers (`WC`, `TIMR`, `GIP`, `GIE`), GPIO, PLL, and global control registers.

Control flow and integration: consumed primarily by `cthw20k1.c` for indirect register access through `hw_read_20kx` and `hw_write_20kx`. Higher-level resource managers never include this map directly; they call function pointers in `struct hw`.

State and persistence: constants only; no state.

Risks and test signals: register typos directly misprogram hardware. Notable risk: large dense macro set is hard to validate without hardware. Test signal is successful 20K1 card init, SRC enable, I2S/S/PDIF routing, timer interrupts, and stable playback/capture.
