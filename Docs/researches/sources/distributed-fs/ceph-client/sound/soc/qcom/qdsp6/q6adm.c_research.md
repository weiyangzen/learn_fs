# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6adm.c

## Purpose
`q6adm.c` implements the Qualcomm QDSP6 Audio Device Manager driver over APR. It opens and closes COPP objects for AFE ports, reuses matching COPPs through refcounts, maps ASM sessions to COPPs through ADM matrix routing, handles APR responses, and populates child devices under the ADM node.

## Important APIs, types, and functions
Internal state is represented by `struct q6adm` and `struct q6copp`. `q6adm` stores the APR device, service info, per-AFE-port COPP bitmaps, the active COPP list, locking, and matrix-map wait state. `q6copp` stores AFE port, COPP index, DSP COPP ID, topology/mode/rate/bit-width/channel/app metadata, response state, wait queue, kref, and list node.

Exported APIs are `q6adm_open()`, `q6adm_get_copp_id()`, `q6adm_matrix_map()`, and `q6adm_close()`. Important internal functions include `q6adm_alloc_copp()`, `q6adm_find_copp()`, `q6adm_find_matching_copp()`, `q6adm_device_open()`, `q6adm_device_close()`, `q6adm_apr_send_copp_pkt()`, `q6adm_callback()`, and `q6adm_free_copp()`.

## Control flow
Probe allocates `struct q6adm`, records service info, initializes locks/waits/list state, and populates child platform devices. `q6adm_open()` validates the port, searches for an existing matching COPP, or allocates a new COPP index under the list spinlock. It initializes metadata and sends `ADM_CMD_DEVICE_OPEN_V5`; the APR callback records the returned COPP ID and wakes the per-COPP wait queue.

`q6adm_matrix_map()` builds an `ADM_CMD_MATRIX_MAP_ROUTINGS_V5` packet containing one session node and the DSP COPP IDs found from the route payload. It sends the packet under `adm->lock` and waits for `ADM_CMD_MATRIX_MAP_ROUTINGS_V5` completion on `matrix_map_wait`. `q6adm_close()` drops the kref; final release sends device close, clears the COPP bitmap, removes the list node, and frees memory.

## State and persistence behavior
State is in kernel memory only: COPP bitmaps, active list, krefs, response fields, and wait queues. A COPP persists while references exist and is closed on final kref release. DSP-side state persists until ADM close succeeds or the DSP resets. No disk state is used.

## Dependencies and integration points
The driver depends on APR, Q6 core service info, Q6AFE port ID translation, Q6DSP channel mapping, Q6DSP errno values, and ASoC/QDSP6 routing/ASM layers that call ADM APIs. It registers as an APR driver matching `qcom,q6adm` and populates OF children for consumers.

## Risks and test signals
Risks include list traversal in callbacks without taking `copps_list_lock`, possible duplicate matching COPP selection if multiple compatible COPPs exist, and returning `0` from `q6adm_matrix_map()` on an invalid path after logging but without failing immediately. Error paths rely on kref release to close and free partially opened COPPs. Test signals include open/close refcount reuse, invalid port rejection, route mapping for playback and live record, APR timeout/error injection, concurrent opens/closes, and DSP reset behavior.
