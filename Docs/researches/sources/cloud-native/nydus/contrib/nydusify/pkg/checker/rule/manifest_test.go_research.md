# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/manifest_test.go

Purpose: tests `ManifestRule`, the checker rule responsible for validating OCI and Nydus image manifest/config consistency. The file focuses on observable rule behavior: rule naming, ignored deprecated OCI config fields, Nydus target layer layout, OCI diff ID checks, and special model-artifact handling.

Important APIs and flow: `TestManifestName` asserts `ManifestRule.Name()` returns `manifest`. `TestManifestRuleValidate_IgnoreDeprecatedField` builds source and target `parser.Parsed` values with differing `ocispec.ImageConfig.ArgsEscaped` and expects `Validate` to ignore that deprecated field. `TestManifestRuleValidate_TargetLayer` mutates a target Nydus manifest through invalid and valid layer arrangements, checking blob media type, bootstrap annotation, bootstrap reference annotations, and diff ID count. `TestManifestRuleValidateOCI` and `TestManifestRuleValidateNydus` call unexported validation helpers from package-local tests.

State and persistence: tests are pure in-memory construction of OCI descriptors and parser models. No filesystem or registry state is used.

Dependencies and integration: uses `parser.Parsed`, `remote.Remote`, `utils` Nydus media/annotation constants, OCI digest/descriptors, and CloudNativeAI model-spec constants. It verifies that model manifests relax standard rootfs layer count validation and require matching Nydus artifact annotations.

Risks and test signals: coverage is strong for layer classification and model-artifact exceptions, but it uses synthetic descriptors and does not exercise parser-produced real manifests or reference blob annotation parsing beyond string presence.
