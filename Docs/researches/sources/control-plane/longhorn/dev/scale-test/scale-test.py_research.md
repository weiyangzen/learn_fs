<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/dev/scale-test/scale-test.py -->
# sources/control-plane/longhorn/dev/scale-test/scale-test.py

Purpose: development utility for generating many node-pinned StatefulSet manifests and watching pod, PVC, and VolumeAttachment events during Longhorn scale tests.

Important APIs/types/functions: constants configure namespace, node prefix/count, template, kubeconfig, and context. Functions `create_sts_deployment`, `create_sts_yaml`, `watch_pods_async`, `watch_pvc_async`, `watch_va_async`, and event processors use `kubernetes.client`, `config`, and `watch`.

Control flow: on startup it renders 100 StatefulSet YAML files under `out/`, loads kubeconfig, initializes logging and placeholder result maps, starts async watchers for pods, PVCs, and cluster volume attachments, and runs the event loop forever.

State and persistence: writes generated manifests to `out/sts<N>.yaml`. Runtime state is in-memory event processing maps that are currently unused placeholders.

Dependencies/integration points: depends on Python Kubernetes client, kubeconfig access, Kubernetes watch APIs, `StorageV1Api` volume attachments, and `statefulset.yaml` placeholders.

Risks/test signals: watchers are blocking iterators inside async tasks, generated files are relative to cwd, and TODO timing metrics are not implemented. Test signals are generated manifest count/content, kubeconfig loading, event logs during scaling, and eventual enhancement of PVC-to-pod/attachment timing maps.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/dev/scale-test/scale-test.py -->
