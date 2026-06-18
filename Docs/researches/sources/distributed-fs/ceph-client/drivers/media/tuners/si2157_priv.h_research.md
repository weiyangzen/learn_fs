# sources/distributed-fs/ceph-client/drivers/media/tuners/si2157_priv.h

Purpose: private definitions for the Si2157-family tuner driver.

Important APIs and types: defines media pad indices, `struct si2157_dev`, supported part IDs, `struct si2157_tuner_info`, command buffer `struct si2157_cmd`, capability macros `SUPPORTS_1700KHz` and `SUPPORTS_ATV_IF`, and all firmware filename constants.

Control flow: `si2157.c` uses this header to track driver state, choose firmware based on part/ROM ID, bound firmware command argument length, and branch analog/bandwidth behavior by chip capability. Media pad definitions are used only when media-controller support is compiled.

State and persistence: `struct si2157_dev` holds the mutex that serializes command transport, frontend pointer, active/inversion/firmware flags, part and IF port IDs, cached IF/bandwidth/frequency, delayed stats work, and optional media entity state.

Dependencies and integration points: includes firmware loading, V4L2 media-controller helpers, and the public `si2157.h`. It is private to the module and should not be used by board drivers.

Risks: firmware filename constants are part of userspace deployment expectations; renaming or incorrect fallback selection can break devices. `SI2158_50_FIRMWARE` points to a `si2178`-named file, which may be intentional legacy naming but is easy to misread. The command buffer has a hard 30-byte limit that all opaque command arrays must respect.

Test signals: compile-time coverage of all part-specific firmware declarations, firmware request tests for old and new names, and probe logs confirming detected part IDs map to expected capability branches.
