<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom-pbs.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom-pbs.c

Purpose: provides a small Qualcomm PMIC PBS client driver API. It lets consumers find a PBS device through DT and trigger PMIC PBS RAM sequences by setting scratch bits, issuing a software trigger, and waiting for acknowledgement bits.

Important APIs/types/functions: `struct pbs_dev` holds device, parent regmap, mutex, optional consumer device link, and base offset. Exported functions are `qcom_pbs_trigger_event()` and `get_pbs_client_device()`. Internal `qcom_pbs_wait_for_ack()` polls `PBS_CLIENT_SCRATCH2` for a bit or error value. Probe reads the parent SPMI regmap and the child `reg` base address.

Control flow: a consumer calls `get_pbs_client_device()`, which parses `qcom,pbs`, finds the platform device, retrieves drvdata, creates an autoremove supplier device link, and returns the PBS handle. To trigger events, `qcom_pbs_trigger_event()` validates a nonzero bitmap, serializes on `pbs->lock`, clears a stale `0xff` error in `SCRATCH2`, then for each requested bit clears the ACK bit, sets the corresponding `SCRATCH1` bit, sets the software trigger bit in `TRIG_CTL`, polls for ACK/NACK, clears scratch bits, and finally clears all requested `SCRATCH1` bits.

State and persistence: runtime state is minimal: base register offset, regmap, lock, and the most recent device link pointer. Hardware scratch registers carry transient request/ack/error state. No persistent storage is maintained.

Dependencies and integration: depends on OF phandles, platform devices, parent PMIC regmap, SPMI-style child layout, device links, and public `<linux/soc/qcom/qcom-pbs.h>`. Consumer drivers are responsible for defining the PBS phandle and using bitmaps agreed with PMIC PBS firmware.

Risks and test signals: if multiple consumers call `get_pbs_client_device()`, the single `pbs->link` field is overwritten, although links are autoremove supplier links; this is mostly a bookkeeping risk. `qcom_pbs_wait_for_ack()` treats exactly `0xff` as NACK and otherwise any requested bit as success, so mixed error/ack values need firmware validation. Cleanup ignores errors from final scratch clears. Test signals include missing phandle deferral, parent regmap absence, valid device link creation, multi-bit bitmap ordering, timeout after roughly `DELAY * RETRIES`, NACK clearing, concurrent triggers serialized by the mutex, and correct scratch register cleanup after failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom-pbs.c -->
