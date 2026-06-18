# sources/distributed-fs/ceph-client/net/qrtr/smd.c

## Purpose
`smd.c` implements the QRTR endpoint transport over Qualcomm SMD/RPMSG channels.

## Important APIs, Types, And Functions
The per-device wrapper is `struct qrtr_smd_dev`. Main functions are `qcom_smd_qrtr_callback()`, `qcom_smd_qrtr_send()`, `qcom_smd_qrtr_probe()`, and `qcom_smd_qrtr_remove()`. The driver matches RPMSG service `"IPCRTR"`.

## Control Flow
Probe allocates state, stores the RPMSG endpoint, sets QRTR endpoint `xmit`, registers with QRTR using auto node id, and stores drvdata. RPMSG receive callback fetches drvdata and posts inbound data to QRTR; invalid QRTR packets are logged but reported as consumed so RPMSG drops them. QRTR transmit linearizes the skb and sends bytes through `rpmsg_send()`, consuming the skb on success or freeing it on failure. Remove unregisters the endpoint and clears drvdata.

## State And Persistence
State is devm-managed per RPMSG device, with QRTR endpoint state existing between probe and remove. There is no persistent storage.

## Dependencies And Integration Points
The file depends on RPMSG driver APIs, QRTR endpoint APIs, and skb linearization. It is built as `qrtr-smd` when `CONFIG_QRTR_SMD` is enabled.

## Risks
The driver must return `0` for invalid received packets after logging, otherwise lower layers may retry/drop differently than intended. `rpmsg_send()` and `skb_linearize()` failures must free the skb. Remove must not race with callbacks using drvdata.

## Test Signals
Tests should cover probe/register failure, inbound valid and invalid packet handling, transmit success/failure skb ownership, no-drvdata callback behavior, and remove cleanup.
