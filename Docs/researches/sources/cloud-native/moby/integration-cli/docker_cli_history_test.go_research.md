# sources/cloud-native/moby/integration-cli/docker_cli_history_test.go

Purpose: integration tests for `docker history`, including build-layer ordering, behavior for existing and missing images, commit comments, and human/non-human size formatting.

Important APIs/types/functions: `DockerCLIHistorySuite`; tests `TestBuildHistory`, `TestHistoryExistentImage`, `TestHistoryNonExistentImage`, `TestHistoryImageWithComment`, `TestHistoryHumanOptionFalse`, and `TestHistoryHumanOptionTrue`.

Control flow: the build-history test builds an image with labels A-Z, reads history output, and expects newest layer ordering Z through A. Comment tests create and commit a container with `-m`, then parse the first history row. Size-format tests locate the `SIZE` column from the header and validate each row as either an integer byte count or human-readable value.

State and persistence: creates images and a committed container image. History output reflects image layer metadata and commit comments stored in image history.

Dependencies and integration points: Docker build helper, minimal base image selection, `docker history`, commit command, regex parsing, and CLI text table layout.

Risks: the file explicitly calls `TestBuildHistory` a heisen-test because image created timestamps and sort behavior can be unpredictable. Table parsing by whitespace and column offsets can break if CLI formatting changes.

Test signals: failures point to image history ordering regressions, missing commit comments, incorrect error behavior for missing images, or broken `--human` size rendering.
