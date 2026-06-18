## sources/cloud-native/buildkit/util/progress/progress_test.go

Purpose: tests core progress context behavior and nested writer propagation.

Important tests: `TestProgress` verifies code can run without progress, then with a progress context/writer carrying metadata, and confirms captured items all include metadata. `TestProgressNested` runs nested synchronous and parallel calculations, reads progress until EOF, and verifies final last-by-ID statuses.

Support functions: `calc` emits start/calculating/done statuses; `reduceCalc` creates nested writers and parallel goroutines; `saveProgress` drains a reader.

Risks covered: metadata propagation, nested writer creation, reader EOF after cancellation/close, collapsed final statuses. Gaps: cancellation errors, writing after close, no-op writer, and MultiReader/MultiWriter are not directly tested here.
