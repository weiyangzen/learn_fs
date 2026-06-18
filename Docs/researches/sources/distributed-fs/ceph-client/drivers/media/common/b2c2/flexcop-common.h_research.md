# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-common.h

## Purpose
This is the common private header for B2C2 FlexCop PCI/USB DVB device support. It defines core shared data structures, logging macros, initialization state bits, callback contracts, and cross-file prototypes.

## Important APIs, Types, and Functions
Key types are `struct flexcop_dma`, `struct flexcop_i2c_adapter`, and `struct flexcop_device`. `flexcop_device` aggregates device identity, DVB adapter/frontend/demux/net/dmxdev state, three I2C adapters, feed/filter state, bus-specific callbacks for IBI register access, I2C requests, streaming control, and MAC retrieval. The header declares prototypes for common device lifecycle, DMA, EEPROM MAC check, I2C, SRAM, frontend init/exit, revision naming, hardware filtering, SMC, and MAC filter control.

## Control Flow
Bus-specific drivers allocate/fill `flexcop_device`, provide callbacks, then call common initialization. Common components coordinate through the structure and state bits such as `FC_STATE_DVB_INIT`, `FC_STATE_I2C_INIT`, and `FC_STATE_FE_INIT`.

## State and Persistence
The structure holds all shared runtime state for a FlexCop adapter. EEPROM MAC data can be read into `dvb_adapter.proposed_mac`, but the header itself does not persist data.

## Dependencies and Integration Points
It depends on `flexcop-reg.h`, DVB demux/net/frontend APIs, PCI DMA types, mutexes, and I2C. It is included by common and bus-specific FlexCop sources.

## Risks and Test Signals
Because callbacks are bus-specific, initialization must verify all required function pointers before use. Tests should cover lifecycle state-bit cleanup, feedcount/PID filtering transitions, I2C adapter indexing, and proposed MAC propagation.
