# sources/cloud-native/nydus/contrib/nydusify/pkg/provider/logger.go

Purpose: defines progress logging abstraction and a default logrus implementation for conversion/provider workflows.

Important APIs/types/functions: `LoggerFields`, `ProgressLogger`, `defaultLogger`, `defaultLogger.Log`, and `DefaultLogger`.

Control flow: `Log` ensures a non-nil field map, logs the start message, records the current time, and returns a closure. The closure adds a `"Time"` field with elapsed duration, logs the same message again, and returns its input error unchanged.

State and persistence: logging state is transient. The closure mutates the provided `fields` map by adding `"Time"`.

Dependencies and integration points: logrus and callers that use deferred completion logging around conversion steps.

Risks and test signals: mutating caller-provided fields can affect reused maps. The logger does not encode success/failure beyond returning the error; callers must include error fields themselves if desired.
