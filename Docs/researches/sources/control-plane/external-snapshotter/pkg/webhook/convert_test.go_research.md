# sources/control-plane/external-snapshotter/pkg/webhook/convert_test.go

Purpose: golden-file tests for group snapshot content conversion between v1beta1 and v1beta2.

Important APIs/functions: `TestFromBeta1ToBeta2`, `TestFromBeta2ToBeta1`, and `fromFile`.

Control flow: tests glob matching beta1 YAML files, derive paired beta2 filenames by string replacement, load both as unstructured objects, run the relevant conversion function, emulate API version assignment by the framework, and compare with semantic deep equality. Failures print JSON-formatted actual/expected objects.

State and persistence: reads YAML testdata only; no API server or network.

Dependencies and integration: depends on filepath globbing, sigs YAML decoding, unstructured objects, semantic equality, and the conversion code.

Risks and test signals: good signal for expected object transformations and annotation preservation. The glob-driven pairing depends on strict filename conventions and does not exercise the HTTP conversion review framework or malformed annotation errors.
