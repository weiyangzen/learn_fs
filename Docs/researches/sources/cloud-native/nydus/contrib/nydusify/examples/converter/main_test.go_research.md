# sources/cloud-native/nydus/contrib/nydusify/examples/converter/main_test.go

## Purpose
This test ensures the converter example constructs the expected `converter.Opt` and calls `converter.Convert`.

## Important APIs, Types, and Functions
It monkeypatches `converterpkg.Convert`, invokes example `main`, and asserts selected option fields.

## Control Flow
The patch replaces conversion with a function that checks work dir, binary path, source, target, insecure flags, and platform. Then `main()` is called directly.

## State, Persistence, and Dependencies
No real conversion or persistence happens. Dependencies are `gomonkey`, `testify/require`, and the converter package.

## Integration Points
It guards the example from drifting away from converter API expectations.

## Risks and Test Signals
The test does not validate all options in the example, and it depends on monkeypatch support. It is a narrow wiring test, not an end-to-end conversion signal.
