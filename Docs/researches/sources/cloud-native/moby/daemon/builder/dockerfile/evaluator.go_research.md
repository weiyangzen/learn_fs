## sources/cloud-native/moby/daemon/builder/dockerfile/evaluator.go

**Purpose:** Defines the dispatch jump table and per-stage dispatch state for classic Dockerfile evaluation.

**Important APIs/types:** `dispatch`, `dispatchState`, `newDispatchState`, `stagesBuildResults`, `newStagesBuildResults`, `getByName`, `validateIndex`, `get`, `checkStageNameAvailable`, `commitStage`, `dispatchRequest`, `newDispatchRequest`, `updateRunConfig`, `hasFromImage`, `beginStage`, and `setDefaultPath`.

**Control flow:** `dispatch` performs platform checks, builds environment with allowed build args, expands single-word commands, defers intermediate container cleanup according to options, and switches on concrete instruction type. Stage result lookup supports names and numeric indexes while rejecting current-stage self-reference.

**State and persistence:** `dispatchState` holds mutable run config, maintainer, image ID, base image, stage name, build args, and OS. Stage results persist run configs in memory for later `COPY --from` and `FROM <stage>`.

**Dependencies and integration:** Connects BuildKit parser instruction types to dispatcher functions, builder options, OCI default path env, image OS checks, and error definitions.

**Risks:** Cleanup defers run after every dispatch and depend on `Remove`/`ForceRemove`. Stage indexing has subtle boundary behavior. Default PATH injection affects image config and cache results.

**Test signals:** `evaluator_test.go` covers dispatch routing. Dispatcher and internals tests cover state-copy behavior and stage-related cases.
