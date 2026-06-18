# sources/distributed-fs/ceph-client/drivers/pmdomain/actions/owl-sps-helper.c

Purpose: shared low-level register helper for Actions Owl Smart Power System power gates.

Important APIs/types/functions: exports `owl_sps_set_pg(void __iomem *base, u32 pwr_mask, u32 ack_mask, bool enable)`. It manipulates `OWL_SPS_PG_CTL` at offset 0, using separate request and acknowledgement masks.

Control flow: the helper reads current control state, returns immediately if ack already equals the requested state, sets or clears the power request bits, writes back, polls every 50 us up to about 5 ms for the ack bits to match, delays 10 us after success, and returns `-ETIMEDOUT` on failure.

State and persistence: no software state. Hardware power-gate and ack bits persist in the SPS register until changed by this or firmware/hardware.

Dependencies/integration: used by `owl-sps.c` and exported GPL for other Actions SPS users. Depends on MMIO access and delay helpers.

Risks: polling assumes ack polarity equals requested enable state and that 5 ms is sufficient. Concurrent writers to the same SPS register could race because this helper has no lock. Mask mistakes can alter unrelated power domains.

Test signals: power on/off each domain and verify ack transitions, timeout behavior on blocked hardware, and no unintended changes to neighboring bits.
