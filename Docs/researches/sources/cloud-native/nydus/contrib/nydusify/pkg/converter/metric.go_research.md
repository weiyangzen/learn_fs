# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/metric.go

Purpose: writes conversion metrics to JSON.

Important APIs and flow: `dumpMetric` creates/truncates the target file, JSON-encodes a `converter.Metric`, wraps create and encode errors, and closes the file on return.

State and persistence: writes one JSON metrics file.

Dependencies and integration: called by `Convert` when `Opt.OutputJSON` is nonempty. Uses Harbor acceleration-service metric type.

Risks and test signals: caller ignores `dumpMetric` errors in `Convert`, so metric write failures do not fail conversion. Parent directories must already exist.
