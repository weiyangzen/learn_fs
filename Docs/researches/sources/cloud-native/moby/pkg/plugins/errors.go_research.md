<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/errors.go -->
# sources/cloud-native/moby/pkg/plugins/errors.go

Purpose: defines plugin client status errors and helpers for classifying HTTP 404 responses. Important APIs are `statusError.Error`, `IsNotFound`, and `isStatusError`. Control flow checks concrete `*statusError` type and status code; `Error` formats method and remote error text. State is error value fields. Dependencies are fmt and net/http. Risks include lack of `errors.As` support for wrapped status errors and losing status in formatted output. Test signal is through client tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/errors.go -->
