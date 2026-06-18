# sources/cloud-native/moby/integration/image/prune_test.go

Purpose: integration tests for image prune safety, deletion order, used-image preservation, and negative label filters.

Important APIs and helpers: `TestPruneDontDeleteUsedDangling`, `TestPruneLexographicalOrder`, `TestPruneDontDeleteUsedImage`, and `TestPruneLabelFilterNegative`. They use sub-daemons, `ImagePrune`, `ImageInspect`, `ImageTag`, container helpers, special images, and filter maps.

Control flow: dangling test loads a dangling image, creates a container using it, prunes dangling images, and ensures the used image remains. Lexical order test tags busybox many times, removes latest, runs a container by image ID, prunes unused tagged images, and expects a retained tag. Used-image test table-drives single vs two tags and multiple image reference forms, then prunes with `dangling=false` and verifies only unused aliases disappear. Negative label test loads labeled and unlabeled images, prunes with `label!` and `dangling=false`, and checks only the unlabeled image is deleted and reported.

State and persistence: exercises image reference graph state, container-to-image references, labels, prune reports, and tag selection/deletion order.

Dependencies and integration: depends on local sub-daemons, snapshotter-specific digest reference behavior, specialimage labeled/dangling builders, image prune filters, and error classification.

Risks: skipped for Windows or remote daemons. Behavior differs between graphdriver and snapshotter for digest references. Prune report ordering/fields are part of asserted behavior.

Test signals: strong safety signal that prune does not delete images used by containers and correctly handles aliases, labels, and dangling state.
