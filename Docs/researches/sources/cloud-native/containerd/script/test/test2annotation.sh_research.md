<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/test/test2annotation.sh -->
# sources/cloud-native/containerd/script/test/test2annotation.sh

- Purpose: Converts Go test JSON-style output to GitHub Actions annotations using a jq program.
- Important behavior: Locates `test2annotation.jq` beside the script and pipes input through jq.
- Control flow and state: Stateless filter; input is stdin and output is annotated text.
- Dependencies and integration: Requires `jq` and the adjacent jq script. Used in CI to surface test failures inline.
- Risks: Fails if jq or the jq program is missing; only handles formats supported by that jq filter.
- Test signals: Annotation output in GitHub Actions logs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/test/test2annotation.sh -->
