# sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/src/elasticsearch/elasticsearch.yml

Purpose: Minimal Elasticsearch benchmark override forcing a single-node cluster.
Important APIs/types/functions: declarative configuration keys include `discovery.type: single-node`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Bind-mounted by `hello.py` when benchmarking `elasticsearch:8.1.1`.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
