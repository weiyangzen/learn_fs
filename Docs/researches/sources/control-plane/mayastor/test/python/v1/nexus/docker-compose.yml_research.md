# sources/control-plane/mayastor/test/python/v1/nexus/docker-compose.yml

Purpose: four-node v1 nexus test topology. Services `ms0` to `ms3` run io-engine on static `10.1.0.2` through `10.1.0.5`.

Important configuration: all nodes enable ANA, NVMe reservations, ASAN leak suppression, repo and `/tmp` mounts, hugepages, and SPDK capabilities. `ms0` uses cores `1,2`; `ms1`, `ms2`, and `ms3` use single cores `2`, `3`, and `4`. `ms3` additionally sets `NVME_KATO_MS=1000` and `NEXUS_DONT_READ_LABELS=true` for null-device nexus tests.

State, dependencies, and integration: the topology supports remote replicas on `ms1`/`ms2`, local/remote nexus targets on `ms0`/`ms3`, null bdev tests, failover tests, and reservation tests. Static IPs and `mayastor_net` are consumed by `v1.mayastor` fixtures.

Risks and test signals: core overlap between `ms0` and `ms1` can affect timing-sensitive tests. Host requirements include hugepages, NVMf, and Docker privileges. Compose success is validated by downstream nexus, fio, and NVMe CLI tests.
