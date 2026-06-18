# sources/distributed-fs/lizardfs/tests/dispatcher/Dockerfile

## Purpose
This Dockerfile packages the Flask test dispatcher service in a minimal Python 3.10 image.

## Important APIs, Types, and Functions
It creates a non-root `runner` user, sets `/code` as workdir, configures `FLASK_APP`, exposes port 5000, installs `requirements.txt`, copies the dispatcher tree, and starts waitress with `--threads=1 --call app:create_app`.

## Control Flow
Docker build installs dependencies before copying the app source, improving cache reuse. Container start launches waitress serving the factory-created Flask app.

## State and Persistence Behavior
The image has no volume or persistence. Dispatcher queues remain in process memory and vanish on restart.

## Dependencies and Integration Points
It depends on `python:3.10-slim`, `requirements.txt`, waitress, Flask app factory, and Docker Compose port mapping.

## Risks and Edge Cases
Single-thread waitress matches the app's unsynchronized in-memory queue but limits concurrency. No healthcheck, authentication, or persistent store is configured.

## Test Signals
Build and container smoke tests should verify dependency install, non-root execution, `/` response, and queue behavior through mapped port 5000.
