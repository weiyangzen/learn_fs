# sources/cloud-native/buildkit/client/connhelper/npipe/npipe_windows.go

Purpose: Windows implementation for `npipe://` URLs using Windows named pipes.

Important APIs/types/functions: build tag `windows`; `Helper` parses the URL by splitting on `://`, converts forward slashes to backslashes, and returns a dialer calling `winio.DialPipeContext`.

Control flow: invalid URL strings without a scheme separator are rejected. Valid URLs produce a connection helper whose dialer uses the caller’s context for pipe dialing.

State and persistence: no persistent state; connects to OS named pipe endpoints.

Dependencies/integration points: `github.com/Microsoft/go-winio`, shared `connhelper`, URL parsing, and BuildKit daemon endpoints exposed over Windows named pipes.

Risks/test signals: address conversion is simple string manipulation after URL stringification, so unusual URL escaping or authority/path forms should be handled cautiously. No direct tests in this subset.
