# sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/reboot_store.sh

Purpose: Resets and starts Podman plus stargz-store benchmark storage.
Important APIs/types/functions: `retry`, `kill_all`, `cleanup`; env flags `DISABLE_PREFETCH`, `DISABLE_ESTARGZ`, and `LOG_FILE`.
Control flow: kills store processes, unmounts/removes store data, resets Podman, rewrites store config, writes Podman `storage.conf`, optionally starts `stargz-store`, and waits for the pool link.
State and persistence: clears `/var/lib/stargz-store`, rewrites `/etc/containers/storage.conf`, and resets Podman state.
Dependencies and integration points: integrates Podman overlay storage `additionallayerstores` with stargz-store's mounted reference store.
Risks: destructive cleanup and broad process killing require isolated containers; failed unmounts can leave state behind.
Test signals: exercised by benchmark mode `BENCHMARK_RUNTIME_MODE=podman`.
