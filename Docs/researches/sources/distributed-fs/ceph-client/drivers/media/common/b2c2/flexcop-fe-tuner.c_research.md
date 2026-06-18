# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-fe-tuner.c

## Purpose
This file detects and attaches DVB frontends/tuners/LNB controllers for B2C2 FlexCop-based cards. It supports multiple SkyStar, AirStar, CableStar, and SkyStar S2 variants by trying a table of attach functions.

## Important APIs, Types, and Functions
The exported APIs are `flexcop_frontend_init` and `flexcop_frontend_exit`. Helper functions include firmware request bridging, voltage/tone/DiSEqC control, sleep wrapping, board-specific frontend attach routines, symbol-rate setup for STV0299, and demod init tables for MT352/STV0297. The `FE_SUPPORTED` macro compiles attach paths only when the corresponding frontend drivers are reachable.

## Control Flow
`flexcop_frontend_init` iterates `flexcop_frontends`, sets `fc->dev_type` before each try, calls the attach function against `fc_i2c_adap[0]`, detaches partial frontends on failure, and registers the first successful frontend with the DVB adapter. Attach functions may configure `no_base_addr`, attach demodulators, tuner PLLs, LNB controllers, tune I2C clocking, override frontend ops, and set workarounds such as skipped PID filters. Exit unregisters and detaches the frontend if initialized.

## State and Persistence
Runtime state changes include `fc->fe`, `fc->fe_sleep`, `fc->dev_type`, `fc->init_state`, `fc_i2c_adap[*].no_base_addr`, and `skip_6_hw_pid_filter`. No persistent storage is written. Firmware may be requested for supported demods through `request_firmware`.

## Dependencies and Integration Points
The file integrates with many DVB frontend/tuner drivers: MT312, STV0299, S5H1420, ITD1000, CX24113/23/20, ISL6421, MT352, BCM3510, NXT200X, LGDT330X, simple tuner, DVB PLL, and STV0297. It relies on FlexCop IBI register callbacks for LNB voltage/tone and I2C adapters for attachment.

## Risks and Test Signals
Board probing is order-dependent and mutates state before success; failed paths must reset `no_base_addr` and detach partial frontends. Some failure paths after attaching a demod or LNB do not fully undo all changes. Test each supported board combination with reachable modules, failure fallback between attach paths, DiSEqC timing, voltage/tone register writes, frontend registration failure cleanup, firmware request propagation, and `flexcop_frontend_exit`.
