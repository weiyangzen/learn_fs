# sources/cloud-native/moby/integration/image/load_test.go

Purpose: integration test for loading a new image over an existing tag and preserving the old image as dangling.

Important APIs and helpers: `TestLoadDanglingImages` uses `iimage.Load`, `specialimage.MultiLayerCustom`, `ImageList`, and local `findImageByName`/`findImageById` closures.

Control flow: the test loads `namedimage:latest`, records its image ID from `ImageList`, loads a second image under the same tag with different content, lists images again, and asserts the tag points to a new ID while the old ID remains present with no repo tags.

State and persistence: validates image store reference mutation and dangling image retention after tag replacement. The old manifest/content remains reachable by ID without tags.

Dependencies and integration: depends on Linux special image generation, daemon image load behavior, image list response fields, and containerd error definitions for local helper failures.

Risks: skipped outside Linux. It assumes image list returns both tagged and dangling images under default options in the tested mode.

Test signals: protects against losing old image records when loading a replacement tag.
