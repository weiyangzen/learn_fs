# sources/cloud-native/stargz-snapshotter/script/cri-o/test-legacy.sh

Purpose: Runs baseline CRI validation against CRI-O and records images used by tests.
Important APIs/types/functions: `retry`, `cleanup` temp cleanup, CRI-O socket constants, pause image path.
Control flow: starts a privileged CRI-O node, waits for `crictl stats`, runs `critest`, scrapes CRI-O journal for pulled images, appends the pause image, writes the unique image list, and kills the node.
State and persistence: creates a disposable Docker node and temp log/list files; outputs the image list for stargz mirroring.
Dependencies and integration points: depends on Docker, CRI-O, crictl/critest, and the test node image.
Risks: journal parsing is brittle; privileged runtime and tmpfs storage are required.
Test signals: first phase of `cri-o/test.sh`.
