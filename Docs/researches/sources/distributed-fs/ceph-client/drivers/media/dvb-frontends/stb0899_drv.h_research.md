<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_drv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_drv.h

## Purpose
`stb0899_drv.h` is the public configuration and attach interface for the STB0899 multistandard frontend. Board drivers use it to provide init tables, clock/transport settings, postprocess GPIO behavior, DVB-S2 algorithm constants, and tuner callbacks.

## Important APIs, Types, And Functions
It defines table element types `struct stb0899_s1_reg` and `struct stb0899_s2_reg`, IQ inversion enum values, GPIO address constants, postprocess event definitions, `struct stb0899_postproc`, and the large `struct stb0899_config`. The config includes init-table pointers, postproc pointer, inversion default, crystal frequency, demod address, TS output/control options, low/high master-clock settings, DVB-S2 acquisition constants, and tuner callback hooks for frequency, bandwidth, and RF signal gain. `stb0899_attach()` is declared or stubbed depending on Kconfig.

## Control Flow
Board code fills `struct stb0899_config` and calls `stb0899_attach()`. The main driver later walks the table pointers in `.init`, reads clock fields in search, and invokes tuner callbacks through the I2C repeater.

## State And Persistence
The header owns no runtime state, but config objects are retained by pointer inside `struct stb0899_state`. Init tables and callbacks must remain valid for the frontend lifetime.

## Dependencies And Integration Points
It depends on Linux module/kernel headers and `media/dvb_frontend.h`. It is the main integration contract among board files, `stb0899_drv.c`, `stb0899_algo.c`, and external tuner drivers.

## Risks And Test Signals
Because most fields are raw hardware values, misconfiguration can prevent attach, lock, TS output, or safe LNB/GPIO behavior. Callback NULL checks are partial and semantics are board-specific. Test signals are successful build with Kconfig enabled/disabled, attach with stable config storage, init-table sentinel correctness, and tuner callback calls with expected frequency/bandwidth values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_drv.h -->
