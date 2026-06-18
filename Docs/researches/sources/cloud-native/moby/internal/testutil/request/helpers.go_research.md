<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/helpers.go -->
# sources/cloud-native/moby/internal/testutil/request/helpers.go

Purpose: response-body helpers for test HTTP requests. Important APIs are `ReadBody` and generic `ReadJSONResponse[T]`. Control flow always closes bodies after reading, validates `Content-Type` as `application/json` with media-type parsing before JSON decoding, and includes up to 8 KiB of non-JSON body text in the error. State is none beyond consuming/closing response bodies. Dependencies are `encoding/json`, `mime`, and HTTP types. Risks include callers losing access to the body after helper use and strict content-type requirements. Test signal is covered by `helpers_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/helpers.go -->
