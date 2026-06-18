# sources/distributed-fs/ceph-client/sound/soc/codecs/sigmadsp-regmap.c

Purpose: regmap transport adapter for the shared SigmaDSP firmware loader. It lets codec drivers use an existing regmap for SigmaDSP memory/control transactions instead of open-coded bus I/O.

Important APIs and data: `sigmadsp_write_regmap()` calls `regmap_raw_write(control_data, addr, data, len)`. `sigmadsp_read_regmap()` calls `regmap_raw_read()`. `devm_sigmadsp_init_regmap()` delegates firmware parsing/allocation to `devm_sigmadsp_init()`, then stores the regmap in `control_data` and installs the raw read/write callbacks.

Control flow: parent codec drivers call the exported initializer with their device, regmap, optional safeload ops, and firmware name. The SigmaDSP core later invokes these callbacks while loading firmware data blocks, applying cached controls, or reading byte controls.

State and persistence: no local state beyond the callback pointers stored in `struct sigmadsp`. Regcache, bus locking, endianness, and address formatting are inherited from the supplied regmap.

Dependencies and integration points: depends on regmap raw access semantics, the core `sigmadsp` parser/control layer, and GPL exports for codec modules. Risks include using raw regmap operations on regmaps not configured for the DSP memory layout, cache side effects if callers provide a cached regmap, and lack of transport-specific validation. Test signals include firmware load through an actual codec regmap, readback controls, safeload fallback behavior, and regmap error propagation.
