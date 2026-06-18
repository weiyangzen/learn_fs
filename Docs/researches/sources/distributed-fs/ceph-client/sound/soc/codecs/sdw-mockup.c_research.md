# sources/distributed-fs/ceph-client/sound/soc/codecs/sdw-mockup.c

Purpose: mock SoundWire ASoC codec for host/controller tests where the bus needs a simple full-duplex slave model. It registers one DAI with DP1 playback and DP8 capture and advertises mock SoundWire properties for several reserved Intel part IDs.

Important APIs and data: `struct sdw_mockup_priv` stores the `sdw_slave`. The ASoC DAI ops implement `.set_stream`, `.hw_params`, `.hw_free`, and `.shutdown`. SoundWire slave ops implement `.read_prop`, `.interrupt_callback`, `.update_status`, and `.bus_config`. The driver marks `slave->is_mockup_device = true`.

Control flow: SoundWire probe allocates private data, attaches it to the slave device, marks the slave mock, and registers the ASoC component/DAI. `set_stream` stores the SoundWire stream runtime as DMA data. `hw_params` rejects missing stream/slave, converts PCM params to SoundWire stream/port config, selects port 1 for playback or port 8 for capture, and calls `sdw_stream_add_slave()`. `hw_free` removes the slave from the stream and shutdown clears DMA data. `read_prop` populates no paging, one sink port and one source port, allocates DPN property arrays, sets full-port type and simple channel preparation, and marks simple clock stop capable.

State and persistence: all state is runtime-only: DMA stream pointer, `sdw_slave`, and allocated property arrays. No register map, firmware, or persistent configuration exists.

Dependencies and integration points: SoundWire bus/core, ASoC SoundWire helpers, PCM params conversion, and mock device IDs. Risks include intentionally arbitrary port allocation, minimal status/interrupt handling, and limited channel/rate constraints. Test signals are SoundWire enumeration by each mock ID, stream add/remove calls, DP1/DP8 direction behavior, property allocation, and host-side bus tests using mock devices.
