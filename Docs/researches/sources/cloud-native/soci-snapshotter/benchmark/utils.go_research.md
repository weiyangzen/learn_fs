## sources/cloud-native/soci-snapshotter/benchmark/utils.go

Purpose: shared benchmark image descriptor model, container creation options, workload loading, and default workload list.

Important APIs/types/functions: `ImageDescriptor`, `ImageOptions`, `Timeout`, `ContainerOpts`, `GetImageList`, `GetImageListFromJSON`, `GetCommitHash`, and `GetDefaultWorkloads`.

Control flow: descriptor JSON is decoded into workload structs; `ContainerOpts` converts image options into containerd `NewContainerOpts` plus OCI spec options for mounts, GPU, env, shm, and host networking.

State and persistence: reads JSON workload files and invokes `git rev-parse HEAD`; otherwise no durable state.

Dependencies and integration: containerd client and OCI helpers, NVIDIA runtime spec helpers, default public ECR workload images, and benchmark drivers.

Risks and test signals: `ContainerOpts` panics if hostname lookup fails for host network mode. Default workload digests can drift if upstream images change. No direct tests here in this subset.
