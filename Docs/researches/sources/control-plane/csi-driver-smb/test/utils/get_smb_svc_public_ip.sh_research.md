# sources/control-plane/csi-driver-smb/test/utils/get_smb_svc_public_ip.sh

## Purpose
This script extracts the public IP of the `smb-server` service from the default namespace.

## Important APIs, Types, And Functions
It runs `kubectl get svc smb-server -n default | grep smb | awk '{print $4}'`.

## Control Flow
With `set -e`, any kubectl or grep failure exits the script. Successful output is the fourth column of kubectl table output.

## State, Persistence, And Dependencies
No state is changed. It depends on kubectl, service existence, and table column layout.

## Integration Points
`suite_test.go` uses this for Windows clusters to rewrite SMB source to `//<public-ip>/share`.

## Risks And Test Signals
The table parser is brittle and does not wait for load balancer ingress. A pending IP can propagate into tests. Signal is stdout containing the IP or script failure.
