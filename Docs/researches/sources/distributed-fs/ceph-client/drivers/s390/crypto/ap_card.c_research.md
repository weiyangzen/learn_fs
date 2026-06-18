## sources/distributed-fs/ceph-client/drivers/s390/crypto/ap_card.c

Purpose: implements AP card device allocation and card-level sysfs attributes. It presents hardware type/function/configuration/counter state for each AP adapter discovered by the bus.

Important APIs/types/functions: `ap_card_create()` allocates and initializes `struct ap_card`. Sysfs attributes include `hwtype`, `raw_hwtype`, `depth`, `ap_functions`, `request_count`, `requestq_count`, `pendingq_count`, `modalias`, `config`, `chkstop`, and `max_msg_size`.

Control flow: bus scan calls `ap_card_create()` with TAPQ hardware info and compatible type, fills device parent/bus/name, and registers the device. Attribute reads aggregate queue counters under `ap_queues_lock` or report cached card hardware info. `config_store()` calls SCLP configure/deconfigure and emits a config uevent.

State and persistence: card state stores raw and compatible AP type, TAPQ hardware info, id, max message size, config/checkstop flags, and total request count. Queue counters remain per queue but are aggregated for card attributes.

Dependencies and integration: uses AP bus structures, global queue hash, SCLP AP configure/deconfigure, Linux device attributes, and AP uevents from `ap_bus.c`.

Risks and test signals: risks include stale config state if SCLP succeeds but later scan disagrees, counter aggregation races, and max message size calculation from hardware ML field. Test sysfs reads, request-count reset, card configure/deconfigure, uevents, and device release after bus removal.
