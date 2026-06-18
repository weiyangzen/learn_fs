# Research: sources/distributed-fs/ipfs-kubo/codecov.yml

Purpose: Codecov service configuration for Kubo coverage reporting.

Important APIs/types/functions: YAML config excludes legacy CI hosts, accepts GitHub CI, requires two builds before notification, sets coverage range to `50...100`, project threshold to `0.2%`, patch threshold to `2%`, and disables comments.

Control flow, state, and persistence: This file has no runtime control flow. It affects external Codecov status checks and notifications when coverage is uploaded.

Dependencies and integration points: Consumed by Codecov infrastructure, not Go code. It integrates with CI coverage upload jobs outside this subset.

Risks and test signals: Threshold changes can make CI noisier or too permissive. Because comments are off, coverage feedback depends on status checks or Codecov UI. No local tests apply.
