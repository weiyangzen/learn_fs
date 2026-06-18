# sources/distributed-fs/ceph-client/sound/hda/controllers/cix-ipbloq.c

## Purpose
`cix-ipbloq.c` supports the CIX Sky1 IPBLOQ HD-audio controller as a platform device. It wraps the generic `azx` HDA engine with CIX-specific reset, clock, reserved-memory, aligned-MMIO, polling, DMA address-offset, and runtime-PM policy.

## Important APIs, Types, and Functions
`struct cix_ipbloq_hda` embeds `struct azx`, device/MMIO pointers, one reset, and two clocks (`ipg`, `per`). Main functions are `cix_ipbloq_hda_probe()`, `cix_ipbloq_hda_create()`, `cix_ipbloq_hda_init()`, `cix_ipbloq_hda_probe_codec()`, runtime/system PM callbacks, remove, and shutdown.

## Control Flow
Probe allocates driver state, acquires reset and clocks, sets a 32-bit DMA mask, optionally binds reserved memory, creates an ALSA card, initializes `azx`, enables runtime PM, resumes the device, initializes MMIO/IRQ/streams/chip, probes/configures codecs, registers the card, and releases the runtime PM reference. Runtime resume enables clocks, toggles reset, and reinitializes the chip if already running.

## State and Persistence Behavior
Persistent runtime state is the embedded `azx`, clock/reset handles, bus flags, stream pages, and card private data. The bus is forced into polling/non-interrupt command handling because `RIRBSTS.RINTFL` cannot be cleared. `bus.core.addr_offset` applies a host-to-HDAC DMA address adjustment for Sky1.

## Dependencies and Integration Points
The driver depends on OF matching (`cix,sky1-ipbloq-hda`), Linux reset/clock frameworks, reserved memory, platform IRQ/MMIO resources, ALSA card lifecycle, and shared `azx` helpers.

## Risks
Runtime suspend disables clocks after stopping/resetting the link; resume error paths after enabling clocks or asserting reset do not explicitly undo prior steps in the same callback. Polling mode is required to avoid interrupt storms, so interrupt assumptions from generic code must not leak in. The fixed negative address offset and 32-bit DMA mask are platform-specific correctness points.

## Test Signals
Validate OF binding, clock/reset acquisition, reserved-memory optional behavior, codec detection, polling-mode operation without interrupt storms, runtime suspend/resume clock/reset sequencing, playback/capture after resume, and non-empty ALSA card registration with model-derived shortname.
