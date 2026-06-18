<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/client_responsehook.go -->
# sources/cloud-native/moby/client/client_responsehook.go

Purpose: implements a transport wrapper that invokes configured `ResponseHook` callbacks after each successful underlying HTTP round trip.

Important APIs/types/functions: private `responseHookTransport` with `base http.RoundTripper`, `hooks []ResponseHook`, and `RoundTrip`.

Control flow: `RoundTrip` delegates to `base.RoundTrip`; if an error occurs it returns immediately without invoking hooks. For non-error responses it invokes hooks in stored order and returns the original response unchanged.

State and integration behavior: no persistence. Hook slices are cloned in `New`, so later mutation of the config slice does not affect the installed transport. Hooks must not consume or close the body; this file does not enforce that contract.

Risks and test signals: risks are hook side effects on response bodies and transport wrapping order with OpenTelemetry. `client_options_test.go` covers option validation and hook installation at construction.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/client_responsehook.go -->
