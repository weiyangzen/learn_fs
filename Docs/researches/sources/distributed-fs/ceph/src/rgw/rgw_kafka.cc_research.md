# sources/distributed-fs/ceph/src/rgw/rgw_kafka.cc

See the grouped research section in `Docs/researches/groups/subset-b-006989_research.md` for the complete report.

This file implements RGW Kafka notification publishing with librdkafka: connection identity/hashing, producer creation for plaintext/SSL/SASL/mTLS, async message queue, topic cache, delivery callbacks, counters, idle connection cleanup, and global manager wrappers. State is process-local manager/connection/topic/callback/queue data; Kafka delivery is the external effect. It depends on librdkafka, RGW URL parsing, Ceph config/logging/time, Boost hash and lock-free queues. Risks include credential handling, cleartext secret opt-in, iterator/concurrency assumptions, shutdown races, callback overflow after produce success, and idle cleanup of pending callbacks. Tests should cover security configs, limits, callback paths, idle deletion, shutdown, and metrics.
