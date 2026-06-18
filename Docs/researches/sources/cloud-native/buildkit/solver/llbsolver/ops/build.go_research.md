# sources/cloud-native/buildkit/solver/llbsolver/ops/build.go

Purpose: implements nested LLB build operations. A `BuildOp` reads an LLB definition file from an input rootfs and delegates solving to the frontend LLB bridge.

Important APIs/types/functions: `BuildOp`, `NewBuildOp`, `CacheMap`, `Exec`, `Acquire`, and `IsProvenanceProvider`. Cache identity is `buildkit.build.v0` plus the serialized `pb.BuildOp`; dependency slots mirror vertex inputs. `Exec` currently accepts only `pb.LLBBuilder`.

Control flow: `Exec` finds the special LLB definition input, validates its input index and worker ref type, mounts the immutable ref readonly, opens the default or overridden LLB definition filename, reads it with `llb.ReadFrom`, unmounts, and calls `FrontendLLBBridge.Solve`. It releases all non-primary refs from the nested result and returns the primary ref result.

State/persistence: no durable state beyond cache refs produced by the delegated solve. Local mount lifecycle is carefully managed: unmount on failure via deferred cleanup, explicit unmount before nested solve on success.

Dependencies/integration: relies on `containerd/continuity/fs.RootPath`, `client/llb`, `frontend.FrontendLLBBridge`, worker refs, snapshot local mounter, and `opsutils.Validate`.

Risks: nested builds are marked as provenance providers but `captureProvenance` currently treats `BuildOp` as incomplete materials. Definition file path handling must stay rooted to prevent escape. Only one primary output is propagated; extra refs are released.

Test signals: no direct tests in this subset. Behavior is covered indirectly through frontend/build solve integration.
