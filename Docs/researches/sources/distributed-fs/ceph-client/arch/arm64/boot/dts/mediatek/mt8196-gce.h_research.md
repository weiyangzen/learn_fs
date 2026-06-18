# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt8196-gce.h

## Purpose

`mt8196-gce.h` is the MT8196 Global Command Engine devicetree binding header. It names GCE thread priority values, hardware event IDs, software synchronization tokens, resource lock tokens, GPR token ranges, and timer token ranges used by CMDQ/GCE clients. The file has 449 macro definitions and no executable code.

The header documents two event spaces. GCE0 is mainly display-oriented: display stream SOF/frame-done windows, WDMA/postmask/mutex/MDP reset events, DISP1 DSI/DP/DVO events, MML0/1 events, overlay events, DPC diagnostics, DPTX/eDPTX events, TE inputs, power-ack windows, and DSI/SPI aliases. GCE1 is mainly non-display: VENC instances, VDEC events, image pipeline events, camera events, SMI assertions, and image/camera QoS/QoF windows. It also defines software tokens for display sequencing, GPR register backup sets, image-system pools and power handshakes, secure-thread notification, user/poll/lock tokens, TZMP tokens, prebuilt lock tokens, and GPR timer tokens.

## Important APIs And Types

The exported API is a collection of integer macros. `CMDQ_THR_PRIO_LOWEST` through `CMDQ_THR_PRIO_HIGHEST` define priorities 0 through 7; lower-priority threads run only when no higher-priority thread is active and same-priority threads are round-robin scheduled. Hardware event macros are either fixed IDs or parameterized range helpers such as `CMDQ_EVENT_DISP0_STREAM_SOF(n)`, `CMDQ_EVENT_DISP1_DISP_DSI1_ENG_EVENT(n)`, `CMDQ_EVENT_IMG_QOF_ACK_EVENT(n)`, and `CMDQ_EVENT_CAM_SENINF_CFG_DONE_EVENT(n)`.

The software token API includes fixed tokens such as `CMDQ_SYNC_TOKEN_CONFIG_DIRTY`, `CMDQ_SYNC_TOKEN_STREAM_EOF`, `CMDQ_SYNC_TOKEN_ESD_EOF`, `CMDQ_SYNC_RESOURCE_WROT0`, and image-system power tokens, plus range helpers such as `CMDQ_SYNC_TOKEN_GPR_SET(n)`, `CMDQ_SYNC_TOKEN_IMGSYS_POOL(n)`, and `CMDQ_TOKEN_GPR_TIMER_R(n)`. Consumers pass these numeric IDs to CMDQ packet wait/clear/set APIs rather than interacting with C objects from this header.

## Control Flow, State, And Persistence

The header has no local control flow. It affects runtime command flow when client drivers embed event or token IDs into CMDQ packets. At runtime, the GCE firmware/hardware waits for, clears, or sets these IDs as command packets execute. State lives in the GCE event/token machinery, not in this file. Persistence is limited to DTS/kernel source ABI and compiled code or DTBs that reference these constants.

## Dependencies And Integration Points

There is no include dependency beyond the header guard. The integration points are MediaTek CMDQ/GCE client drivers, especially display, MML/MDP, overlay, DPTX/eDPTX, encoder/decoder, image pipeline, camera, SMI, secure-world/TZMP, and prebuilt-command users. Numeric values must match the MT8196 hardware event wiring and the CMDQ driver's expectations. Parameterized macros rely on callers passing indices in the documented range; the C preprocessor does not enforce bounds.

## Risks And Test Signals

The key risk is numeric collision or mismatch. Event IDs and software tokens share hardware-visible namespaces, and the file intentionally contains aliases or overlaps in the common-token area, such as `CMDQ_SYNC_TOKEN_TPR_LOCK` sharing 942 with `CMDQ_SYNC_TOKEN_USER_1` and `CMDQ_SYNC_TOKEN_TZMP_DISP_WAIT` sharing 943 with `CMDQ_SYNC_TOKEN_POLL_MONITOR`. Those overlaps may be intentional ABI compatibility but must be reviewed before changing. Parameterized windows can also generate invalid IDs if callers pass out-of-range `n`.

Validation signals include building MT8196 CMDQ clients, boot logs from the CMDQ/GCE driver, display pipeline tests exercising SOF/frame-done/mutex/TE tokens, MML/MDP and overlay reset/frame-done tests, DPTX/eDPTX hotplug or stream tests, camera and image pipeline frame completion tests, VENC/VDEC completion paths, secure-world token handshakes, and timeout-path tests using GPR timer tokens. Static review should check that documented contiguous ranges do not collide unexpectedly and that every changed ID is reflected in hardware documentation and client usage.
