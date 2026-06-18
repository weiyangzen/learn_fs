# sources/distributed-fs/ceph-client/drivers/ata/sata_gemini.h

## Purpose
`sata_gemini.h` declares the public bridge interface for Gemini SATA support. It lets other ATA code hold an opaque `struct sata_gemini *`, query mux/enable state, and start or stop a selected bridge.

## Important APIs, Types, and Functions
The header forward-declares `struct sata_gemini`, defines `enum gemini_muxmode` values `GEMINI_MUXMODE_0` through `GEMINI_MUXMODE_3`, and declares `gemini_sata_bridge_get()`, `gemini_sata_bridge_enabled()`, `gemini_sata_get_muxmode()`, `gemini_sata_start_bridge()`, and `gemini_sata_stop_bridge()`.

## Control Flow, State, and Persistence
This header has no runtime flow or storage itself. Its declarations represent bridge state owned by `sata_gemini.c`; callers receive an opaque pointer, query whether a given ATA controller is bridged to SATA, and bracket hardware use with start/stop calls.

## Dependencies and Integration Points
The declarations are shared between the Gemini bridge platform driver and ATA host drivers that need to coordinate muxing and bridge clocks. The header uses standard kernel C types such as `bool`, relying on includers to have basic type definitions available.

## Risks and Test Signals
Risks include callers treating the opaque pointer as always available instead of handling `ERR_PTR(-EPROBE_DEFER)`, mismatching bridge indexes with mux mode semantics, and forgetting to stop a bridge after start. Build coverage should include both the bridge driver and its consumers; runtime tests should validate all exported symbol users handle absent or deferred bridge state and correctly honor mux-mode enablement.
